import AppKit

/// Renders pixel-art sprite frames with nearest-neighbor scaling.
///
/// Performance-optimized (M10):
/// - Caches CGImage references to eliminate per-draw allocations
/// - Advances from the coordinator's clock, keeping poses and travel in sync
/// - Nearest-neighbor filtering for zero blur
/// - Per-pixel alpha hit testing for transparent click-through
final class SpriteView: NSView {

    /// The current animation frames to cycle through.
    private(set) var frames: [NSImage] = []

    /// Cached CGImage representations of the animation frames for zero-allocation rendering.
    private var cgFrames: [CGImage] = []

    /// Index of the currently displayed frame.
    private(set) var currentFrameIndex: Int = 0

    /// Whether the sprite is horizontally flipped (facing left).
    var isFacingLeft: Bool = false {
        didSet {
            if oldValue != isFacingLeft {
                needsDisplay = true
            }
        }
    }

    /// Callback invoked when the sprite is clicked.
    var onClicked: (() -> Void)?

    private var animationFPS: Double = 0
    private(set) var animationElapsed: TimeInterval = 0

    enum Effect { case none, yarn, sleep }
    var effect: Effect = .none
    var usesWalkBob = false

    /// Whether the current animation should loop.
    private var animationLoops: Bool = true

    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("Not implemented")
    }

    private func setupLayer() {
        wantsLayer = true
        // Nearest-neighbor filtering for crisp pixel art
        layer?.magnificationFilter = .nearest
        layer?.minificationFilter = .nearest
    }

    // MARK: - Animation Control

    /// Sets the animation frames and starts playback.
    ///
    /// - Parameters:
    ///   - frames: Array of NSImage frames.
    ///   - fps: Frames per second for animation.
    ///   - loop: Whether to loop the animation.
    func setAnimation(frames: [NSImage], fps: Double, loop: Bool = true, elapsed: TimeInterval = 0) {
        stopAnimation()

        self.frames = frames
        self.cgFrames = frames.compactMap { img in
            img.cgImage(forProposedRect: nil, context: nil, hints: nil)
        }
        self.currentFrameIndex = 0
        self.animationLoops = loop
        self.animationFPS = max(0, fps)
        self.animationElapsed = max(0, elapsed)

        updateAnimation(deltaTime: 0)
        needsDisplay = true
    }

    /// Stops the current animation.
    func stopAnimation() {
        animationFPS = 0
    }

    func updateAnimation(deltaTime: TimeInterval) {
        guard !cgFrames.isEmpty else { return }
        animationElapsed += max(0, deltaTime)
        let frame = Int((animationElapsed * animationFPS + 0.000000001).rounded(.down))
        let nextIndex = animationLoops ? frame % cgFrames.count : min(frame, cgFrames.count - 1)
        if nextIndex != currentFrameIndex {
            currentFrameIndex = nextIndex
            needsDisplay = true
        }
    }

    // MARK: - Drawing

    override func draw(_ dirtyRect: NSRect) {
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }
        guard currentFrameIndex < cgFrames.count else {
            ctx.clear(bounds)
            return
        }

        ctx.clear(bounds)
        ctx.interpolationQuality = .none

        let cgImage = cgFrames[currentFrameIndex]

        ctx.saveGState()

        if isFacingLeft {
            // Flip horizontally: translate to right edge, scale X by -1
            ctx.translateBy(x: bounds.width, y: 0)
            ctx.scaleBy(x: -1, y: 1)
        }

        let bob: CGFloat = usesWalkBob && currentFrameIndex % 2 == 1 ? bounds.height / 32 : 0
        ctx.draw(cgImage, in: bounds.offsetBy(dx: 0, dy: bob))
        drawEffect(in: ctx)
        ctx.restoreGState()
    }

    /// Small code-native pixel props; the artist's source images stay untouched.
    private func drawEffect(in ctx: CGContext) {
        guard effect != .none else { return }
        ctx.saveGState()
        ctx.setShouldAntialias(false)
        ctx.scaleBy(x: bounds.width / 32, y: bounds.height / 32)
        switch effect {
        case .yarn:
            let x = CGFloat(3 + [0, 1, 2, 1][currentFrameIndex % 4])
            ctx.setFillColor(CGColor(red: 0.29, green: 0.16, blue: 0.36, alpha: 1))
            ctx.fill(CGRect(x: x, y: 2, width: 6, height: 4))
            ctx.fill(CGRect(x: x + 1, y: 1, width: 4, height: 6))
            ctx.setFillColor(CGColor(red: 0.77, green: 0.46, blue: 0.73, alpha: 1))
            ctx.fill(CGRect(x: x + 1, y: 2, width: 4, height: 4))
            ctx.setFillColor(CGColor(red: 0.95, green: 0.69, blue: 0.86, alpha: 1))
            ctx.fill(CGRect(x: x + 1, y: 4, width: 3, height: 1))
            ctx.fill(CGRect(x: x + 3, y: 2, width: 1, height: 3))
            ctx.fill(CGRect(x: x + 5, y: 1, width: 4, height: 1))
        case .sleep:
            ctx.setFillColor(CGColor(red: 0.67, green: 0.77, blue: 0.86, alpha: 1))
            for (x, y) in [(23, 24), (27, 28)] {
                ctx.fill(CGRect(x: x, y: y, width: 3, height: 1))
                ctx.fill(CGRect(x: x + 1, y: y + 1, width: 1, height: 1))
                ctx.fill(CGRect(x: x, y: y + 2, width: 3, height: 1))
            }
        case .none: break
        }
        ctx.restoreGState()
    }

    // MARK: - Click Handling

    override func mouseDown(with event: NSEvent) {
        let locationInView = convert(event.locationInWindow, from: nil)
        if isOpaquePixel(at: locationInView) {
            onClicked?()
        }
    }

    override func hitTest(_ point: NSPoint) -> NSView? {
        let localPoint = convert(point, from: superview)
        guard bounds.contains(localPoint) else { return nil }

        if isOpaquePixel(at: localPoint) {
            return self
        }
        return nil
    }

    // MARK: - Pixel Hit Testing

    private func isOpaquePixel(at point: NSPoint) -> Bool {
        guard currentFrameIndex < cgFrames.count else { return false }

        let cgImage = cgFrames[currentFrameIndex]
        let imageWidth = cgImage.width
        let imageHeight = cgImage.height

        var pixelX = Int(point.x / bounds.width * CGFloat(imageWidth))
        let bob: CGFloat = usesWalkBob && currentFrameIndex % 2 == 1 ? bounds.height / 32 : 0
        let pixelY = imageHeight - 1 - Int((point.y - bob) / bounds.height * CGFloat(imageHeight))

        if isFacingLeft {
            pixelX = imageWidth - 1 - pixelX
        }

        guard pixelX >= 0, pixelX < imageWidth, pixelY >= 0, pixelY < imageHeight else { return false }

        guard let dataProvider = cgImage.dataProvider,
              let data = dataProvider.data,
              let ptr = CFDataGetBytePtr(data) else { return false }

        let bytesPerPixel = cgImage.bitsPerPixel / 8
        let bytesPerRow = cgImage.bytesPerRow
        let offset = pixelY * bytesPerRow + pixelX * bytesPerPixel

        let alphaIndex = bytesPerPixel - 1
        let alpha = ptr[offset + alphaIndex]

        return alpha > 20
    }

    deinit {
        stopAnimation()
    }
}
